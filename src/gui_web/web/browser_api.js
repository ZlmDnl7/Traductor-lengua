if (!window.pywebview && window.location.protocol !== "file:") {
  const api = new Proxy({ __browser: true }, {
    get(target, method) {
      if (method in target) return target[method];
      return (...args) => fetch(`/api/${method}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(args),
      }).then(async (response) => {
        const body = await response.text();
        let result = {};
        try{
          result = body ? JSON.parse(body) : {};
        }catch(error){
          result = {};
        }
        if (!response.ok){
          throw new Error(`HTTP ${response.status}`);
        }
        return result;
      });
    },
  });
  window.pywebview = { api };
  window.__browserDeployment = true;
}
