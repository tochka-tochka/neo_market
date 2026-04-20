import { API_URL, authorized } from "$lib";
import type { PageLoad } from "../$types";

export const load: PageLoad = async ({ params }) => {
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
		const product = res.product;
		return { product: product };
	} catch (error) {
		console.log(error);
	}
};
