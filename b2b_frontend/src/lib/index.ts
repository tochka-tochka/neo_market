import { goto } from "$app/navigation";
import { env } from "$env/dynamic/public";

export const API_URL = env.PUBLIC_DJANGO_URL;

export function authorized(fn: typeof fetch) {
	return async (
		input: RequestInfo | URL,
		init?: RequestInit,
	): Promise<Response> => {
		if (!localStorage.getItem("token")) {
			throw new Error("Not logged in");
		}

		const token = localStorage.getItem("token");

		init = init ?? {};

		let headersObj: Record<string, string> = {};

		if (init.headers instanceof Headers) {
			init.headers.forEach((value, key) => {
				headersObj[key] = value;
			});
		} else if (Array.isArray(init.headers)) {
			init.headers.forEach(([key, value]) => {
				headersObj[key] = value;
			});
		} else if (init.headers) {
			headersObj = { ...init.headers };
		}

		headersObj["Authorization"] = `Bearer ${token}`;

		init.headers = headersObj;

		const res = await fn(input, init);

		if (res.status === 401) {
			console.log("Token expired");
			goto("auth/login");
		}

		return res;
	};
}
