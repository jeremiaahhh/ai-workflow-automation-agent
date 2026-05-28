declare module "sonner" {
  import type * as React from "react";

  export interface ToastOptions {
    description?: React.ReactNode;
    duration?: number;
    id?: string | number;
  }

  type ToastFn = (message: React.ReactNode, options?: ToastOptions) => string | number;

  interface Toast extends ToastFn {
    success: ToastFn;
    error: ToastFn;
    info: ToastFn;
    warning: ToastFn;
    message: ToastFn;
    loading: ToastFn;
    dismiss: (id?: string | number) => void;
  }

  export const toast: Toast;

  export interface ToasterProps {
    position?:
      | "top-left"
      | "top-right"
      | "bottom-left"
      | "bottom-right"
      | "top-center"
      | "bottom-center";
    richColors?: boolean;
    closeButton?: boolean;
    theme?: "light" | "dark" | "system";
    expand?: boolean;
    duration?: number;
  }

  export const Toaster: React.FC<ToasterProps>;
}
