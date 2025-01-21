class DelayManager {
    constructor() {
        this.debounces = {}
        this.throttles = {}
    }

    debounce(id, func, wait) {
        if (!(id in this.debounces)) {
            this.debounces[id] = window.debounce(func, wait)
        }

        this.debounces[id]()
    }

    throttle(id, func, wait) {
        if (!(id in this.throttles)) {
            this.throttles[id] = window.throttle(func, wait)
        }

        this.throttles[id]()
    }
}

window.delay_manager = new DelayManager()
