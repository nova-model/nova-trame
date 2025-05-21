class RevoGrid {
    constructor(id, modelKey, dataKey, stateKey) {
        this.id = id
        this.modelKey = modelKey
        this.dataKey = dataKey
        this.stateKey = stateKey

        this.grid = document.querySelector(`#${this.id}`)
        this.grid.addEventListener('viewportscroll', () => {
            this.updateCheckboxes()
        })
    }

    updateCheckboxes() {
        const trameState = window.trame.state.state
        const modelValue = _.get(trameState, this.modelKey)
        const availableData = _.get(trameState, this.dataKey)
        const selectAllCheckbox = this.grid.querySelector(".header-content input")
        const rowCheckboxes = this.grid.querySelectorAll(".rgCell")

        if (selectAllCheckbox === null) {
            return
        }

        if (modelValue.length === 0) {
            selectAllCheckbox.checked = false
            selectAllCheckbox.indeterminate = false
        } else if (modelValue.length === availableData.length) {
            selectAllCheckbox.checked = true
            selectAllCheckbox.indeterminate = false
        } else {
            selectAllCheckbox.checked = false
            selectAllCheckbox.indeterminate = true
        }

        rowCheckboxes.forEach((element) => {
            const input = element.querySelector('input')

            const rowIndex = element.dataset.rgrow
            input.checked = modelValue.includes(availableData[rowIndex].path)
        })
    }

    cellTemplate(createElement, props) {
        const inputVNode = createElement('input', {
            type: 'checkbox',
            onChange: (e) => {
                const trameState = window.trame.state.state
                const modelValue = _.get(trameState, this.modelKey)
                const path = props.data[props.rowIndex].path
                const index = modelValue.indexOf(path)

                // We need to assign instead of modifying in place in order for the Trame watcher to pick up changes.
                if (e.target.checked && index < 0) {
                    _.set(trameState, this.modelKey, _.concat(modelValue, path))
                } else if (index >= 0) {
                    _.set(trameState, this.modelKey, modelValue.toSpliced(index, 1))
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
