declare module "react" {
  export type ReactNode = unknown;
  export function useMemo<T>(factory: () => T, dependencies: readonly unknown[]): T;
  export function useState<T>(initialState: T): [T, (nextState: T | ((currentState: T) => T)) => void];
}
