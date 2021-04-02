(() => {
	// grab all the relevant elements
	let groupIdInput = document.getElementById("group-id");
	let subgroupNoInput = document.getElementById("subgroup-id");
	let downloadButton = document.getElementById("download");
	let spinner = document.getElementById("spinner");
	let message = document.getElementById("message");

	// listen for clicks on download button
	downloadButton.addEventListener("click", async () => {
	    let url = `http://0.0.0.0:8080/${groupIdInput.value}/${subgroupNoInput.value}`;
	    message.innerHTML = "Расписание загружается. Иногда это может занять до 40 секунд.";

	    let shouldBreak = false;
	    while (!shouldBreak) {
	        // hide button, show spinner
	        downloadButton.style.display = "none";
	        spinner.style.display = "initial";

	        // wait for a fetch, but not less than the delay
	        await Promise.all([
                new Promise(async resolve => {
	                let response = await fetch(url);
                    // 200 = fetched file
                    // 202 = waiting for file to be prepared
                    // ignore 202, break on anything else
                    if (response.status !== 202) {
                        // show button, hide spinner
                        downloadButton.style.display = "initial";
                        spinner.style.display = "none";

                        if (response.status === 200) {
                            message.innerHTML = "";
                            let blob = await response.blob();
                            let file = window.URL.createObjectURL(blob);
                            window.location.assign(file);
                        } else {
                            // status codes besides 200 and 202 signify errors
                            // hopefully they're returned by the backend itself
                            // so showing the response text to the user
                            message.innerHTML = await response.text();
                        }

                        // can't break from inside fetch callback,
                        // putting up flag to break
                        shouldBreak = true;
                    }
                        resolve();
                }),
                // delay by n milliseconds
                new Promise(resolve => setTimeout(resolve, 10000))
            ]);
        }
    });
})();