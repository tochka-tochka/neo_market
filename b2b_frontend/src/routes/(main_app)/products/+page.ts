import { API_URL, authorized } from "$lib";
import type { ProductType } from "$lib/types";
import type { PageLoad } from "./$types";

export const load: PageLoad = async ({ fetch }) => {
	try {
		const res = await authorized(fetch)(`${API_URL}/products/my/`).then((res) =>
			res.json(),
		);
		const products: ProductType[] = res.products;
		return { products: products ?? [] };
	} catch (error) {
		console.error("Error fetching products:", error);
		return { products: [] };
	}
};
