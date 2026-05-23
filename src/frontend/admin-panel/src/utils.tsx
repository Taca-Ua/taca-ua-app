export const navigateBack = ( navigate: any, defaultPath: string) => {


  // Verifica se há histórico para voltar e se o referenciador é diferente da URL atual
  if (window.history.length > 1 && window.history.state.idx > 0) {
    window.history.back();
  } else {
    navigate(defaultPath);
  }
};
