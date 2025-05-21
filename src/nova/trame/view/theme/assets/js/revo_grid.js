window.rvOnMount = function(id, modelKey, dataKey) {
    const grid = document.querySelector(`#${id}`)
    grid.addEventListener('viewportscroll', () => {
        window.rvUpdateCheckboxes(modelKey, dataKey)
    })
}

window.rvUpdateCheckboxes = function(modelKey, dataKey) {
    const trameState = window.trame.state.state
    const modelValue = _.get(trameState, modelKey)
    const availableData = _.get(trameState, dataKey)
    const selectAllCheckbox = document.querySelector(".header-content input")
    const rowCheckboxes = document.querySelectorAll(".rgCell")

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
        input = element.querySelector('input')
        rowIndex = element.dataset.rgrow
        input.checked = modelValue.includes(availableData[rowIndex].path)
    })
}

window.rvCellTemplate = function(createElement, props) {
    const inputVNode = createElement('input', {
        type: 'checkbox',
        onChange: (e) => {
            const trameState = window.trame.state.state
            const modelValue = _.get(trameState, props.column.model_key)
            const path = props.data[props.rowIndex].path
            const index = modelValue.indexOf(path)

            // We need to assign instead of modifying in place in order for the Trame watcher to pick up changes.
            if (e.target.checked && index < 0) {
                _.set(trameState, props.column.model_key, _.concat(modelValue, path))
            } else if (index >= 0) {
                _.set(trameState, props.column.model_key, modelValue.toSpliced(index, 1))
            }

            // Update the UI
            window.rvUpdateCheckboxes(props.column.model_key, props.column.datafiles_key)
            window.trame.state.dirty(props.column.state_key)
        },
    })

    return createElement('label', undefined, inputVNode, props.model[props.prop])
}

window.rvColumnTemplate = function (createElement, props) {
    const inputVNode = createElement('input', {
        type: 'checkbox',
        onChange: (e) => {
            const trameState = window.trame.state.state
            const availableData = _.get(trameState, props.datafiles_key)

            if (e.target.checked) {
                _.set(trameState, 'config.selected_files', availableData.map((item) => item.path))
            } else {
                _.set(trameState, 'config.selected_files', [])
            }

            // Update the UI
            window.rvUpdateCheckboxes(props.model_key, props.datafiles_key)
            window.trame.state.dirty(props.state_key)
        },
    })

    return [inputVNode, 'Available Datafiles']
}
