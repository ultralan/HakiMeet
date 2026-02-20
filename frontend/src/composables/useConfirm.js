import { reactive } from 'vue'

const state = reactive({ show: false, msg: '', danger: false, resolve: null })

export function useConfirm() {
  function confirm(msg, danger = false) {
    return new Promise(r => {
      Object.assign(state, { show: true, msg, danger, resolve: r })
    })
  }
  function handle(val) {
    state.show = false
    state.resolve?.(val)
  }
  return { state, confirm, handle }
}
