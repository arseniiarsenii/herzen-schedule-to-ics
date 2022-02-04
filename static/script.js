(async () => {
    // get group id and subgroup elements
    let $groupIdDropdown = $('.ui.dropdown');
    let subgroups = document.querySelectorAll('input[name="subgroup"]');
    // get groups from server
    let groups_dict = await fetch(`/get_valid_groups`)
    groups_dict = await groups_dict.json();
        
    let result = [];
    // for every item in the dict with
    Object.entries(groups_dict).forEach(([key, value]) => {
        // key = group id
        // value = name
        result.push({
            value: key,
            text: `${value} [${key}]`,
            name: `${value} [${key}]`
        });
    });

    // initialize dropdown
    $groupIdDropdown.dropdown({
        values: result,
        placeholder: 'Начните вводить название группы или ID',
        fullTextSearch: 'exact',
        onChange: async (value) => {
            document.querySelector('input[name="subgroup"][value="1"]').checked = true;

            let numberOfSubgroups = await fetch(`/get_subgroups/${value}`);
            numberOfSubgroups = await numberOfSubgroups.text();
            console.log(numberOfSubgroups)
            if (numberOfSubgroups > 0) {
                for (let i = 0; i < subgroups.length; i++) {
                    if (i < numberOfSubgroups) {
                        $(subgroups[i]).closest('.field').css('display', '');
                    } else {
                        $(subgroups[i]).closest('.field').css('display', 'none');
                    }
                }

                document.getElementById('subgroup').style.display = '';
            } else {
                document.getElementById('subgroup').style.display = 'none';
            }
        }
    });

    $groupIdDropdown.removeClass('loading');

	// grab all the relevant elements
	let downloadButton = document.getElementById('download');
	let spinner = document.getElementById('spinner');
	let message = document.getElementById('message');

	// listen for clicks on download button
	downloadButton.addEventListener('click', async () => {
        let groupId = $groupIdDropdown.dropdown('get value');
        if (groupId === '') {
            message.innerHTML = 'Пожалуйста, выберите группу.';
            return;
        }
        let subgroupNo = document.querySelector('input[name="subgroup"]:checked').value;
        let url = `/get_schedule/${groupId}/${subgroupNo}`;
        message.innerHTML = 'Расписание загружается. Иногда это может занять до 40 секунд.';

        let shouldBreak = false;
        while (!shouldBreak) {
	        // hide button, show spinner
            downloadButton.style.display = 'none';
            spinner.style.display = 'initial';

	        // wait for a fetch, but not less than the delay
            await Promise.all([
                new Promise(async resolve => {
                    let response = await fetch(url);
                    // 200 = fetched file
                    // 202 = waiting for file to be prepared
                    // ignore 202, break on anything else
                    if (response.status !== 202) {
                        // show button, hide spinner
                        downloadButton.style.display = 'initial';
                        spinner.style.display = 'none';

                        if (response.status === 200) {
                            message.innerHTML = '';
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