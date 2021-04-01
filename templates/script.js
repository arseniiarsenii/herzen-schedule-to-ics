(() => {
	// grab all the relevant elements
	let groupIdInput = document.getElementById("group-id");
	let subgroupNoInput = document.getElementById("subgroup-id");
	let downloadButton = document.getElementById("download");
	let spinner = document.getElementById("spinner");
	let message = document.getElementById("message");

	// listen for clicks on download button
	downloadButton.addEventListener("click", async () => {
	    let url = `https://127.0.0.1:8080/${groupIdInput.value}/${subgroupNoInput.value}`;
	    // clear message when making new request
	    message.innerHTML = "";

	    let shouldBreak = false;
	    while (!shouldBreak) {
	        // hide button, show spinner
	        downloadButton.style.display = "none";
	        spinner.style.display = "initial";

	        // wait for a fetch, but not less than the delay
	        await Promise.all([
	            fetch(url)
                    .then(response => async () => {
                        // 200 = fetched file
                        // 202 = waiting for file to be prepared
                        if (response.status === 200 || response.status !== 202) {
                            // show button, hide spinner
                            downloadButton.style.display = "initial";
                            spinner.style.display = "none";

                            if (response.status === 200) {
                                let blob = await response.blob();
                                let file = window.URL.createObjectURL(blob);
                                window.location.assign(file);
                            } else if (response.status !== 202) {
                                // status codes besides 200 and 202 signify errors
                                // hopefully they're returned by the backend itself
                                // so showing the response text to the user
                                message.innerHTML = await response.text();
                            }

                            shouldBreak = true;
                        }
                    }),
                new Promise(resolve => setTimeout(resolve, 10000))
            ]);

	        if (shouldBreak) break;
        }
    });
})();