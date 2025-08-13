class RevoGrid {
    constructor(id, modelKey, dataKey, stateKey) {
        this.id = id
        this.modelKey = modelKey
        this.dataKey = dataKey
        this.stateKey = stateKey
        this.lastSelection = null
        this.shiftPressed = false

        this.grid = document.querySelector(`#${this.id}`)
        this.grid.addEventListener('viewportscroll', () => {
            this.updateCheckboxes()
        })

        this.initShiftKeyListeners()
    }

    updateCheckboxes() {
        // Wait for the DOM to update after the Trame state is updated.
        setTimeout(this._updateCheckboxes.bind(this), 10)
    }

    _updateCheckboxes() {
        const trameState = window.trame.state.state
        const modelValue = _.get(trameState, this.modelKey)
        const availableData = _.get(trameState, this.dataKey)
        const selectAllCheckbox = this.grid.querySelector(".header-content input")
        const rowCheckboxes = this.grid.querySelectorAll(".rgCell:first-child")

        if (selectAllCheckbox === null) {
            return
        }

        let allSelected = null
        rowCheckboxes.forEach((element) => {
            const input = element.querySelector('input')

            const rowIndex = element.dataset.rgrow
            if (availableData[rowIndex] !== undefined) {
                input.checked = modelValue.includes(availableData[rowIndex].path)
            } else {
                input.checked = false
            }

            if (allSelected === null && input.checked) {
                allSelected = true
            } else if (!input.checked) {
                allSelected = false
            }
        })

        if (modelValue.length === 0) {
            selectAllCheckbox.checked = false
            selectAllCheckbox.indeterminate = false
        } else if (allSelected === true) {
            selectAllCheckbox.checked = true
            selectAllCheckbox.indeterminate = false
        } else {
            selectAllCheckbox.checked = false
            selectAllCheckbox.indeterminate = true
        }
    }

    cellTemplate(createElement, props) {
        const inputVNode = createElement('input', {
            type: 'checkbox',
            onChange: (e) => {
                const trameState = window.trame.state.state
                const modelValue = _.get(trameState, this.modelKey)
                const path = props.data[props.rowIndex].path
                const index = modelValue.indexOf(path)

                // I use _.set instead of modifying the modelValue in place in order for the Trame watcher to properly detect the change.
                if (e.target.checked && index < 0) {
                    const newIndex = props.data.findIndex((entry) => entry.path === path)

                    if (this.shiftPressed && this.lastSelection !== null) {
                        let newPaths = []
                        // JavaScript doesn't allow a backwards step during slice, so we need to order the start/stop correctly.
                        if (this.lastSelection < newIndex) {
                            newPaths = props.data.slice(this.lastSelection, newIndex + 1)
                        } else {
                            newPaths = props.data.slice(newIndex, this.lastSelection)
                        }
                        // Exclude paths that are already selected to avoid duplicates.
                        newPaths = newPaths.map((entry) => entry.path).filter((path) => !modelValue.includes(path))

                        _.set(trameState, this.modelKey, _.concat(modelValue, newPaths))
                    } else {
                        _.set(trameState, this.modelKey, _.concat(modelValue, path))
                    }

                    this.lastSelection = newIndex
                } else if (index >= 0) {
                    _.set(trameState, this.modelKey, modelValue.toSpliced(index, 1))

                    // Only allow range selection if the last action was to select a file.
                    this.lastSelection = null
                }

                // Update the UI
                this.updateCheckboxes(this.modelKey, this.dataKey)
                window.trame.state.dirty(this.stateKey)
            },
        })

        return createElement('label', undefined, inputVNode, props.model[props.prop])
    }

    columnTemplate(createElement) {
        const inputVNode = createElement('input', {
            type: 'checkbox',
            onChange: (e) => {
                const trameState = window.trame.state.state
                const availableData = _.get(trameState, this.dataKey)

                if (e.target.checked) {
                    _.set(trameState, this.modelKey, availableData.map((item) => item.path))
                } else {
                    _.set(trameState, this.modelKey, [])
                }

                // Update the UI
                this.updateCheckboxes(this.modelKey, this.dataKey)
                window.trame.state.dirty(this.stateKey)
            },
        })

        return [inputVNode, 'Available Datafiles']
    }

    initShiftKeyListeners() {
        window.document.addEventListener('keydown', (e) => {
            this.shiftPressed = e.shiftKey
        })

        window.document.addEventListener('keyup', (e) => {
            if (e.key === 'Shift') {
                this.shiftPressed = false
            }
        })
    }
}

class RevoGridManager {
    constructor() {
        this.grids = {}
    }

    add(id, modelKey, dataKey, stateKey) {
        this.grids[id] = new RevoGrid(id, modelKey, dataKey, stateKey)
    }

    get(id) {
        return this.grids[id]
    }
}

window.grid_manager = new RevoGridManager()
