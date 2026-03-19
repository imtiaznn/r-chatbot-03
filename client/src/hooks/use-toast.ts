import * as React from "react";

const TOAST_LIMIT = 1;
const TOAST_REMOVE_DELAY = 1000000;

type ToasterToast = {
  id: string;
  title?: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactElement;
  variant?: "default" | "destructive";
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
};

type State = {
  toasts: ToasterToast[];
};

let count = 0;

function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER;
  return count.toString();
}

const listeners: Array<(state: State) => void> = [];
let memoryState: State = { toasts: [] };

function dispatch(action: any) {
  memoryState = reducer(memoryState, action);
  listeners.forEach((listener) => listener(memoryState));
}

function reducer(state: State, action: any): State {
  switch (action.type) {
    case "ADD_TOAST":
      return { ...state, toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT) };
    case "UPDATE_TOAST":
      return { ...state, toasts: state.toasts.map((t) => (t.id === action.toast.id ? { ...t, ...action.toast } : t)) };
    case "DISMISS_TOAST":
      return { ...state, toasts: state.toasts.map((t) => (t.id === action.toastId || action.toastId === undefined ? { ...t, open: false } : t)) };
    case "REMOVE_TOAST":
      return { ...state, toasts: action.toastId === undefined ? [] : state.toasts.filter((t) => t.id !== action.toastId) };
    default:
      return state;
  }
}

function toast({ ...props }: Omit<ToasterToast, "id">) {
  const id = genId();
  dispatch({ type: "ADD_TOAST", toast: { ...props, id, open: true, onOpenChange: (open: boolean) => { if (!open) dispatch({ type: "DISMISS_TOAST", toastId: id }); } } });
  return { id, dismiss: () => dispatch({ type: "DISMISS_TOAST", toastId: id }), update: (props: ToasterToast) => dispatch({ type: "UPDATE_TOAST", toast: { ...props, id } }) };
}

function useToast() {
  const [state, setState] = React.useState<State>(memoryState);
  React.useEffect(() => {
    listeners.push(setState);
    return () => { const i = listeners.indexOf(setState); if (i > -1) listeners.splice(i, 1); };
  }, []);
  return { ...state, toast, dismiss: (toastId?: string) => dispatch({ type: "DISMISS_TOAST", toastId }) };
}

export { useToast, toast };
export type { ToasterToast };
