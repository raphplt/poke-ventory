/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Composable pour les appels API
 * Gère automatiquement la base URL et les credentials (cookies httpOnly)
 */
export const useApi = () => {
	const config = useRuntimeConfig();
	const baseURL = config.public.apiBase;

	return {
		/**
		 * Wrapper pour les requêtes GET avec useFetch
		 * Utilise le cache de Nuxt et SSR-friendly
		 */
		get: <T>(url: string, options?: any) => {
			return useFetch<T>(url, {
				baseURL,
				credentials: "include", // Envoie les cookies httpOnly
				...options,
			});
		},

		/**
		 * Wrapper pour les requêtes POST/PUT/DELETE avec $fetch
		 * Pour les mutations qui ne nécessitent pas de cache
		 */
		post: async <T>(url: string, body?: any) => {
			return await $fetch<T>(url, {
				baseURL,
				method: "POST",
				credentials: "include", // Envoie les cookies httpOnly
				headers: {
					"Content-Type": "application/json",
				},
				body,
			});
		},

		put: async <T>(url: string, body?: any) => {
			return await $fetch<T>(url, {
				baseURL,
				method: "PUT",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
				},
				body,
			});
		},
		delete: async <T>(url: string) => {
			return await $fetch<T>(url, {
				baseURL,
				method: "DELETE",
				credentials: "include",
			});
		},
	};
};
