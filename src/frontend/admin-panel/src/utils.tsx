export const navigateBack = ( navigate: any, defaultPath: string) => {

  if (window.history.length > 1 && document.referrer !== window.location.href) {
    window.history.back();
  } else {
    navigate(defaultPath);
  }
};
