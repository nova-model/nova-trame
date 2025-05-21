window.rvCellTemplate = function(createElement, props) {
    const inputVNode = createElement('input', {
        type: 'checkbox',
        onChange: (e) => {
            const state = window.trame.state.state
            const modelKey = props.column.model_key
            const path = props.data[props.rowIndex].path
            const index = _.get(window.trame.state.state, modelKey).indexOf(path)

            if (e.target.checked && index < 0) {
                _.get(state, modelKey).push(path)
            } else if (index >= 0) {
                _.get(state, modelKey).splice(index, 1)
            }

            window.trame.state.dirty('config')
        },
    })

    return createElement('label', undefined, inputVNode, props.model[props.prop])
}

window.rvColumnTemplate = function (createElement, props) {
    const inputVNode = createElement('input', {
        type: 'checkbox',
        onChange: (e) => {
            const state = window.trame.state.state

            if (e.target.checked) {
                _.set(state, 'config.selected_files', _.get(state, props.datafiles_key).map((item) => item.path))
            } else {
                _.set(state, 'config.selected_files', [])
            }

            window.trame.state.dirty('config')
        },
    })

    return [inputVNode, 'Available Datafiles']
}
