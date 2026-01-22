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
            this.updateUI()
        })

        this.initShiftKeyListeners()
    }

    updateUI() {
        // Wait for the DOM to update after the Trame state is updated.
        setTimeout(this._updateUI.bind(this), 10)
    }

    _updateUI() {
        const trameState = window.trame.state.state
        const modelValue = _.get(trameState, this.modelKey)
        const availableData = _.get(trameState, this.dataKey)
        const selectAllCheckbox = this.grid.querySelector('.header-content input')
        const rowCheckboxes = this.grid.querySelectorAll('.rgCell:first-child')
        const labels = this.grid.querySelectorAll('.rgCell label')
        const rowContainer = this.grid.querySelector('.content-wrapper revogr-data')
        const header = this.grid.querySelector('.header-rgRow')

        // When no data is present the header needs more space as that's the only place we can inject no data
        // text. RevoGrid sets the header to a fixed height that needs to be overridden.
        if (labels.length === 0) {
            console.log(header)
            header.style.height = '90px'
        } else {
            header.style.height = '45px'
        }

        // By default, RevoGrid captures and blocks event propagation for horizontal scrolling on this element.
        // We do not want this to happen, since it interferes with our custom horizontal CSS scrolling to show
        // full cell contents. To avoid this, I add my own event that does not call event.stopPropagation. This
        // forces the event to bubble and enables our horizontal scrolling.
        this.grid.querySelector('.vertical-inner').addEventListener('wheel', () => {})

        let maxWidth = this.grid.clientWidth
        labels.forEach((label) => {
            if (label.clientWidth > maxWidth) {
                maxWidth = label.clientWidth
            }
        })
        if (maxWidth === this.grid.clientWidth) {
            // No labels stretch beyond the original width, we need to remove the row padding to prevent unnecessary scrollbar rendering.
            maxWidth -= 32
        } else {
            // A label has stretched beyond the original width, we need to add the row padding to maintain some whitespace at maximum scroll.
            maxWidth += 32
        }
        rowContainer.style.width = `${maxWidth}px`

        if (selectAllCheckbox === null) {
            return
        }

        // RevoGrid doesn't have a notion of v-model. Since we allow programmatic file selection,
        // we need to programmatically check if checkboxes need to be visually checked. This is
        // inexpensive as the data table is virtually rendered so there are a few dozen checkboxes
        // to process at any time.
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
                this.updateUI(this.modelKey, this.dataKey)
                window.trame.state.dirty(this.stateKey)
            },
        })

        const spanNode = createElement('span', {'class': 'cursor-pointer rv-row-text'}, props.model[props.prop])

        return createElement('label', { 'title': props.model[props.prop] }, inputVNode, spanNode)
    }

    columnTemplate(createElement, extensions) {
        const trameState = window.trame.state.state
        const availableData = _.get(trameState, this.dataKey)

        const inputVNode = createElement('input', {
            type: 'checkbox',
            onChange: (e) => {
                if (e.target.checked) {
                    _.set(trameState, this.modelKey, availableData.map((item) => item.path))
                } else {
                    _.set(trameState, this.modelKey, [])
                }

                // Update the UI
                this.updateUI(this.modelKey, this.dataKey)
                window.trame.state.dirty(this.stateKey)
            },
        })

        let extensions_text = ''
        if (extensions.length > 0) {
            extensions_text = ` (${extensions.join(',')})`
        }

        const header = createElement('div', {'class': 'align-center d-flex'}, inputVNode, `Available Datafiles${extensions_text}`)

        let controls = null
        if (availableData.length < 1) {
            controls = createElement('p', {}, 'No files to display.')
        }

        return createElement('div', {'class': 'd-flex flex-column'}, header, controls)
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
