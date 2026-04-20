import { API_URL, authorized } from "$lib";
import type { Char, InvoiceType, ProductType } from "$lib/types";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ depends, fetch }) => {
	depends("invoices:delete", "invoices:accept");
	try {
		const res = await authorized(fetch)(`${API_URL}/invoices/`, {
			headers: {
				Authorization: `Bearer ${localStorage.getItem("token")}`,
			},
			cache: "no-store",
		}).then((res) => res.json());
		const invoices: InvoiceType[] = res.invoices;
		return { invoices: invoices ?? [] };
	} catch (error) {
		console.error("Error fetching invoices:", error);
		return { invoices: [] };
	}
};
