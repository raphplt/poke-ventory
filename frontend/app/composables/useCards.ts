import type { Card, CardFilters } from "~/types/api";

/**
 * Composable pour gérer les cartes Pokémon
 */
export const useCards = () => {
	const api = useApi();

	/**
	 * Récupérer la liste des cartes avec filtres
	 */
	const getCards = (filters?: CardFilters) => {
		const params = new URLSearchParams();

		if (filters?.set_id) params.append("set_id", filters.set_id);
		if (filters?.name) params.append("name", filters.name);
		if (filters?.rarity) params.append("rarity", filters.rarity);
		if (filters?.type) params.append("type", filters.type);
		if (filters?.skip) params.append("skip", filters.skip.toString());
		if (filters?.limit) params.append("limit", filters.limit.toString());

		const queryString = params.toString();
		const url = queryString ? `/cards/?${queryString}` : "/cards/";

		return api.get<Card[]>(url);
	};

	/**
	 * Récupérer une carte par son ID
	 */
	const getCard = (cardId: string) => {
		return api.get<Card>(`/cards/${cardId}`);
	};

	/**
	 * Créer une carte (nécessite authentification)
	 */
	const createCard = async (card: Partial<Card>) => {
		return await api.post<Card>("/cards/", card);
	};

	/**
	 * Mettre à jour une carte (nécessite authentification)
	 */
	const updateCard = async (cardId: string, card: Partial<Card>) => {
		return await api.put<Card>(`/cards/${cardId}`, card);
	};

	/**
	 * Supprimer une carte (nécessite authentification)
	 */
	const deleteCard = async (cardId: string) => {
		return await api.delete(`/cards/${cardId}`);
	};

	return {
		getCards,
		getCard,
		createCard,
		updateCard,
		deleteCard,
	};
};
