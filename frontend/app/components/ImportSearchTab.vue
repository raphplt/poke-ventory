<script setup lang="ts">
interface Props {
	importType: "cards" | "products";
}

interface SearchCard {
	id: string;
	name: string;
	set: string;
	number: string;
}

const props = defineProps<Props>();

const searchQuery = ref("");
const isSearching = ref(false);
const searchResults = ref<SearchCard[]>([]);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);
const selectedCards = ref<Set<string>>(new Set());

const performSearch = async () => {
	if (!searchQuery.value.trim()) {
		errorMessage.value = "Saisis au moins un mot-clé pour lancer la recherche.";
		return;
	}

	isSearching.value = true;
	errorMessage.value = null;
	successMessage.value = null;

	try {
		// TODO: Appel API à implémenter
		// const results = await searchCards(searchQuery.value);
		// searchResults.value = results;

		// Simulation pour l'instant
		await new Promise((resolve) => setTimeout(resolve, 800));
		searchResults.value = [];
		successMessage.value =
			"Recherche effectuée (fonctionnalité en développement).";
	} catch (error: unknown) {
		errorMessage.value =
			error instanceof Error
				? error.message
				: "Une erreur est survenue lors de la recherche.";
	} finally {
		isSearching.value = false;
	}
};

const toggleCardSelection = (cardId: string) => {
	if (selectedCards.value.has(cardId)) {
		selectedCards.value.delete(cardId);
	} else {
		selectedCards.value.add(cardId);
	}
};

const addSelectedCards = async () => {
	if (selectedCards.value.size === 0) {
		errorMessage.value = "Sélectionne au moins une carte à ajouter.";
		return;
	}

	try {
		// TODO: Appel API à implémenter pour ajouter les cartes/produits sélectionnés
		const itemType = props.importType === "cards" ? "carte(s)" : "produit(s)";
		const destination =
			props.importType === "cards" ? "collection" : "inventaire";
		successMessage.value = `${selectedCards.value.size} ${itemType} ajouté(s) à ton ${destination} !`;
		selectedCards.value.clear();
	} catch (error: unknown) {
		errorMessage.value =
			error instanceof Error ? error.message : "Une erreur est survenue.";
	}
};

const resetSearch = () => {
	searchQuery.value = "";
	searchResults.value = [];
	selectedCards.value.clear();
	errorMessage.value = null;
	successMessage.value = null;
};
</script>

<template>
	<div class="space-y-6">
		<div>
			<h2 class="text-xl font-semibold text-gray-900 mb-1">Import par recherche</h2>
			<p class="text-sm text-gray-600">
				{{
					props.importType === "cards"
						? "Recherche des cartes dans notre base de données et ajoute-les à ta collection."
						: "Recherche des produits scellés dans notre base de données et ajoute-les à ton inventaire."
				}}
			</p>
		</div>

		<div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
			<label class="block">
				<span class="text-sm font-medium text-gray-700 mb-2 block">
					{{
						props.importType === "cards"
							? "Rechercher une carte"
							: "Rechercher un produit"
					}}
				</span>
				<div class="flex gap-2">
					<input
						v-model="searchQuery"
						type="text"
						:placeholder="
							props.importType === 'cards'
								? 'Ex: Pikachu, Dracaufeu, Base Set...'
								: 'Ex: Booster Écarlate et Violet, Display Paradoxe...'
						"
						class="flex-1 px-4 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						@keyup.enter="performSearch"
					/>
					<button
						class="px-5 py-2 text-sm font-medium text-white bg-blue-600 rounded-md disabled:opacity-50 hover:bg-blue-700 transition-colors shrink-0"
						:disabled="isSearching || !searchQuery.trim()"
						@click="performSearch"
					>
						{{ isSearching ? "Recherche..." : "Rechercher" }}
					</button>
				</div>
			</label>

			<div class="mt-3 text-xs text-gray-600">
				<p class="font-medium mb-1.5">Conseils de recherche :</p>
				<ul
					v-if="props.importType === 'cards'"
					class="list-disc list-inside ml-3 space-y-0.5"
				>
					<li>Recherche par nom de carte (ex: "Pikachu")</li>
					<li>Recherche par set (ex: "Base Set", "Jungle")</li>
					<li>Recherche par numéro (ex: "025")</li>
				</ul>
				<ul v-else class="list-disc list-inside ml-3 space-y-0.5">
					<li>Recherche par nom de produit (ex: "Booster Écarlate et Violet")</li>
					<li>Recherche par type (ex: "Display", "ETB", "Coffret")</li>
					<li>Recherche par set (ex: "Paradoxe des Forces", "151")</li>
				</ul>
			</div>
		</div>

		<div
			v-if="errorMessage"
			class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
		>
			{{ errorMessage }}
		</div>

		<div
			v-if="successMessage"
			class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700"
		>
			{{ successMessage }}
		</div>

		<div v-if="searchResults.length > 0" class="space-y-4">
			<div class="flex items-center justify-between">
				<h3 class="text-lg font-semibold text-gray-900">Résultats de recherche</h3>
				<button
					v-if="selectedCards.size > 0"
					class="px-4 py-2 text-white bg-emerald-600 rounded hover:bg-emerald-700 transition-colors"
					@click="addSelectedCards"
				>
					Ajouter {{ selectedCards.size }} carte(s)
				</button>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				<div
					v-for="card in searchResults"
					:key="card.id"
					class="rounded border p-4 cursor-pointer transition-all"
					:class="
						selectedCards.has(card.id)
							? 'border-blue-500 bg-blue-50'
							: 'border-gray-200 bg-white hover:border-gray-300'
					"
					@click="toggleCardSelection(card.id)"
				>
					<div class="flex items-center gap-3">
						<input
							type="checkbox"
							:checked="selectedCards.has(card.id)"
							class="text-blue-600"
							@click.stop="toggleCardSelection(card.id)"
						/>
						<div>
							<p class="font-semibold">{{ card.name }}</p>
							<p class="text-sm text-gray-500">{{ card.set }} · #{{ card.number }}</p>
						</div>
					</div>
				</div>
			</div>

			<button
				class="text-sm text-gray-500 underline hover:text-gray-700"
				@click="resetSearch"
			>
				Nouvelle recherche
			</button>
		</div>

		<div
			class="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-700"
		>
			<p class="font-medium mb-0.5">⚠️ Fonctionnalité en développement</p>
			<p>
				La recherche et l'ajout direct de cartes depuis la base de données seront
				bientôt disponibles.
			</p>
		</div>
	</div>
</template>
