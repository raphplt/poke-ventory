<template>
	<div class="container mx-auto p-4">
		<h1 class="text-3xl font-bold mb-6">Test API - Cartes Pokémon</h1>

		<!-- Filtres -->
		<div class="mb-6 space-y-4">
			<div>
				<label class="block text-sm font-medium mb-2">Rechercher par nom</label>
				<input
					v-model="searchName"
					type="text"
					placeholder="Ex: Pikachu"
					class="border rounded px-4 py-2 w-full max-w-md"
					@input="handleSearch"
				/>
			</div>

			<div>
				<label class="block text-sm font-medium mb-2">Filtrer par type</label>
				<select
					v-model="selectedType"
					class="border rounded px-4 py-2"
					@change="handleSearch"
				>
					<option value="">Tous les types</option>
					<option value="Fire">Feu</option>
					<option value="Water">Eau</option>
					<option value="Grass">Plante</option>
					<option value="Electric">Électrique</option>
					<option value="Psychic">Psy</option>
					<option value="Fighting">Combat</option>
					<option value="Darkness">Ténèbres</option>
					<option value="Metal">Métal</option>
					<option value="Dragon">Dragon</option>
					<option value="Fairy">Fée</option>
				</select>
			</div>

			<button
				class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
				@click="handleSearch"
			>
				Rechercher
			</button>
		</div>

		<!-- État de chargement -->
		<div v-if="pending" class="text-center py-8">
			<p class="text-gray-500">Chargement des cartes...</p>
		</div>

		<!-- Erreur -->
		<div
			v-else-if="error"
			class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"
		>
			<p>Erreur : {{ error.message }}</p>
		</div>

		<!-- Liste des cartes -->
		<div
			v-else-if="cards && cards.length > 0"
			class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4"
		>
			<div
				v-for="card in cards"
				:key="card.id"
				class="border rounded-lg p-4 hover:shadow-lg transition-shadow"
			>
				<img
					v-if="card.image"
					:src="card.image + '/high.png'"
					:alt="card.name"
					class="w-full h-auto rounded mb-2"
				/>
				<h3 class="font-bold text-lg">{{ card.name }}</h3>
				<p class="text-sm text-gray-600">N° {{ card.local_id }}</p>
				<div v-if="card.types" class="flex gap-1 mt-2">
					<span
						v-for="type in card.types"
						:key="type"
						class="text-xs bg-gray-200 px-2 py-1 rounded"
					>
						{{ type }}
					</span>
				</div>
				<p v-if="card.rarity" class="text-sm mt-2">
					<span class="font-semibold">Rareté:</span> {{ card.rarity }}
				</p>
				<p v-if="card.illustrator" class="text-xs text-gray-500 mt-1">
					Illustrateur: {{ card.illustrator }}
				</p>
			</div>
		</div>

		<!-- Aucun résultat -->
		<div v-else class="text-center py-8">
			<p class="text-gray-500">Aucune carte trouvée</p>
		</div>

		<!-- Pagination simple -->
		<div v-if="cards && cards.length > 0" class="mt-6 flex justify-center gap-4">
			<button
				class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
				:disabled="pending"
				@click="loadMore"
			>
				Charger plus
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
const { getCards } = useCards();

// État
const searchName = ref("");
const selectedType = ref("");
const currentSkip = ref(0);
const limit = 20;

// Récupération des cartes avec useFetch (réactive et SSR-friendly)
const {
	data: cards,
	pending,
	error,
	refresh,
} = await getCards({
	limit,
	skip: currentSkip.value,
	name: searchName.value || undefined,
	type: selectedType.value || undefined,
});

// Recherche
const handleSearch = async () => {
	currentSkip.value = 0;
	await refresh();
};

// Charger plus
const loadMore = () => {
	currentSkip.value += limit;
	refresh();
};
</script>
