export function mutationName(protein, pos, state) {
    return `${protein}_${pos}${state}`;
}
