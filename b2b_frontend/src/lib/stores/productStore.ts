import { writable } from 'svelte/store';
import type { ProductType } from '$lib/types';

export const currentProduct = writable<ProductType | null>(null);