import { writable } from "svelte/store";
import { browser } from "$app/environment";

const initialToken = browser ? localStorage.getItem("token") : null;

export const token = writable(initialToken);

if (browser) {
	token.subscribe((value) => {
		if (value) {
			localStorage.setItem("token", value);
		} else {
			localStorage.removeItem("token");
		}
	});
}

import { derived } from "svelte/store";
export const isAuthenticated = derived(token, ($token) => !!$token);
