import { API_URL, authorized } from "$lib";
import type { Char, ProductType, SkuType } from "$lib/types/index.js";

export const load = async ({ params }) => {
	try {
		const res = await authorized(fetch)(
			`${API_URL}/products/${params.product_id}`,
			{
				method: "GET",
				headers: {
					Authorization: `Bearer ${localStorage.getItem("token")}`,
				},
			},
		).then((res) => res.json());
		const product: ProductType = res.product;

		const sku = product.skus.filter(
			(sku: SkuType) => sku.id === params.sku_id,
		)[0];

		return {
			product: product,
			sku: sku,
		};
	} catch (error) {
		console.error("Error loading new_sku:", error);
		throw error;
	}
};
