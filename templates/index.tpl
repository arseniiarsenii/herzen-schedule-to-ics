<html>
<head>
   <title>Herzen Schedule Export</title>
   <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.css"></link>
</head>
<body>
    <div><br><br></div>
    <div class="ui centered grid">
    <div class="ui centered raised padded container segment">
        <h1 class="ui center aligned header"><u>Herzen Schedule Export</u></h1>
        <h4 class="ui center aligned header ">Экспорт расписания вашей группы в файл iCalendar (.ics) с возможностью последующего импорта в Google календарь и другие календари.</h2>
        <div class="ui center aligned segment" style="size: inherit;">
            <div class="ui top attached label compact">Данные</div>
            <div> ID группы </div>
            <div class="ui left icon input compact">
                <input id="group-id" type="number" placeholder="12460">
                <i class="users icon"></i>
            </div>
            <div> Номер подгруппы </div>
            <div class="ui left icon input compact">
                <input id="subgroup-id" type="number" placeholder="Если нет - 1">
                <i class="users icon"></i>
            </div>
            <p id="message" align="center"></p>
            <br><br>
            <div class="ui center aligned container">
                <button id="download" class="ui active button">
                    <i class="download icon"></i>
                    Загрузить
                </button>
                <img id="spinner" style="width: 7rem; display: none;" src="https://i.gifer.com/ZZ5H.gif" />
            </div>
            <br>
            <div class="ui raised padded">
                <p align="center">Как найти ID группы:<br><i>https://guide.herzen.spb.ru/static/schedule_dates.php?id_group=<b><u>12460</u></b></i></p>
                <p align="center">Арсений Величко 2021. <a href='https://github.com/arseniiarsenii/herzen-schedule-to-ics'>Код проекта на GitHub<i class="github icon"></i></a></p>
            </div>
        </div>
    </div>
    </div>
    <script>(()=>{let e=document.getElementById("group-id"),t=document.getElementById("subgroup-id"),n=document.getElementById("download"),i=document.getElementById("spinner"),o=document.getElementById("message");n.addEventListener("click",async()=>{let l=e.value,a=t.value,d=`http://0.0.0.0:8080/${l}/${a}`;o.innerHTML="Расписание загружается. Иногда это может занять до 40 секунд.";let s=!1;for(;!s;)n.style.display="none",i.style.display="initial",await Promise.all([new Promise(async e=>{let t=await fetch(d);if(202!==t.status){if(n.style.display="initial",i.style.display="none",200===t.status){o.innerHTML="";let e=await t.blob(),n=`${l}-${a}.ics`;if(window.navigator.msSaveOrOpenBlob)window.navigator.msSaveOrOpenBlob(e,n);else{const t=document.createElement("a");document.body.appendChild(t);const i=window.URL.createObjectURL(e);t.href=i,t.download=n,t.click(),setTimeout(()=>{window.URL.revokeObjectURL(i),document.body.removeChild(t)},0)}}else o.innerHTML=await t.text();s=!0}e()}),new Promise(e=>setTimeout(e,1e4))])})})();</script>
</body>
</html>