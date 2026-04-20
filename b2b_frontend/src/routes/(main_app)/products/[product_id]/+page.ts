import { API_URL, authorized } from "$lib";
import type { ProductType } from "$lib/types";
import type { PageLoad } from "../$types";

export const load: PageLoad = async ({ params, depends, fetch }) => {
	depends("skus:update");
	try {
		const res = await authorized(fetch)(
			`${API_URL}/products/${params.product_id}/`,
			{
				headers: {
					Authorization: `Bearer ${localStorage.getItem("token")}`,
				},
			},
		).then((res) => res.json());
		const product: ProductType = res.product;
		console.log(product);
		if (!product.skus) {
			product.skus = [];
		}
		product.images = product.images.sort((a, b) =>
			a.order > b.order ? 1 : -1,
		);
		return { product: product };
	} catch (error) {
		console.log(error);
	}
};
