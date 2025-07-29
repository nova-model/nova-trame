class DelayManager {
    constructor() {
        this.debounces = {}
        this.throttles = {}
    }

    debounce(id, func, wait, ...args) {
        if (!(id in this.debounces) || this.debounces[id]['wait'] !== wait) {
            this.debounces[id] = {
                'debounce': _.debounce(func, wait),
                'wait': wait
            }
        }

        this.debounces[id]['debounce'](...args)
    }

    throttle(id, func, wait, ...args) {
        if (!(id in this.throttles) || this.throttles[id]['wait'] !== wait) {
            this.throttles[id] = {
                'throttle': _.throttle(func, wait),
                'wait': wait
            }
        }

        this.throttles[id]['throttle'](...args)
    }
}

window.delay_manager = new DelayManager()
