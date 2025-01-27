class DelayManager {
    constructor() {
        this.debounces = {}
        this.throttles = {}
    }

    debounce(id, func, wait, ...args) {
        if (!(id in this.debounces)) {
            this.debounces[id] = window.debounce(func, wait)
        }

        this.debounces[id](...args)
    }

    throttle(id, func, wait, ...args) {
        if (!(id in this.throttles)) {
            this.throttles[id] = window.throttle(func, wait)
        }

        this.throttles[id](...args)
    }
}

window.delay_manager = new DelayManager()
