/**
 * Optional glue when landing + app shell both need a feedback trigger.
 * Only use if the project already depends on zustand — otherwise lift state in App.
 *
 * Copy to e.g. src/store/useFeedbackStore.ts
 */
import { create } from "zustand";

type FeedbackState = {
  open: boolean;
  setOpen: (open: boolean) => void;
};

export const useFeedbackStore = create<FeedbackState>((set) => ({
  open: false,
  setOpen: (open) => set({ open }),
}));
