(async () => {
    // url of the backend
    let serverUrl = "http://0.0.0.0:8080";

    // initialize group id dropdown
    let groupIdDropdown = $(".ui.dropdown");
    let groups = fetch(`${serverUrl}/get_valid_groups`)
        .then(response => response.json())
        .then(groups_dict => {
            let result = [];
            Object.entries(groups_dict).forEach(([key, value]) => {
                result.push({
                    value: key,
                    text: `${value} ${key}`,
                    name: `${value} [${key}]`
                });
            });

            let values = {
                values: result
            }
            groupIdDropdown.dropdown(values);
        });

	// grab all the relevant elements
	let subgroupNoInput = document.getElementById("subgroup-id");
	let downloadButton = document.getElementById("download");
	let spinner = document.getElementById("spinner");
	let message = document.getElementById("message");

	// listen for clicks on download button
	downloadButton.addEventListener("click", async () => {
	    let groupId = groupIdDropdown.dropdown("get value");
	    let subgroupNo = subgroupNoInput.value;
	    let url = `${serverUrl}/${groupId}/${subgroupNo}`;
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
                            let filename = `${groupId}-${subgroupNo}.ics`

                            // downloading file
                            if (window.navigator.msSaveOrOpenBlob) {
                                // download method for IE
                                window.navigator.msSaveOrOpenBlob(blob, filename);
                            } else {
                                // create <a> element
                                const a = document.createElement('a');
                                document.body.appendChild(a);

                                // set it to download the file and click it
                                const url = window.URL.createObjectURL(blob);
                                a.href = url;
                                a.download = filename;
                                a.click();

                                // clean up
                                setTimeout(() => {
                                  window.URL.revokeObjectURL(url);
                                  document.body.removeChild(a);
                                }, 0)
                            }
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