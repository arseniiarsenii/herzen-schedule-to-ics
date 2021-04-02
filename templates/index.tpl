<html>
<head>
    <title>Herzen Schedule Export</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/components/dropdown.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/components/dropdown.min.js" defer></script>
    <script src="static/script.js" defer></script>
</head>
<body>
    <div>
        <br>
        <br>
    </div>
    <div class="ui centered grid">
        <div class="ui centered raised padded container segment">
            <h1 class="ui center aligned header"><u>Herzen Schedule Export</u></h1>
            <h4 class="ui center aligned header ">Экспорт расписания вашей группы в файл iCalendar (.ics) с возможностью последующего импорта в Google календарь и другие календари.</h4>
            <div class="ui center aligned segment" style="size: inherit;">
                <div class="ui top attached label">Данные</div>
                <div>Выберите группу</div>
                <div class="ui fluid search selection dropdown loading">
                    <input type="hidden">
                    <i class="dropdown icon"></i>
                    <div class="default text">Начните вводить название группы или ID</div>
                </div>
                <div> Номер подгруппы </div>
                <div class="ui fluid left icon input">
                    <input id="subgroup-id" placeholder="Если нет - 1">
                    <i class="users icon"></i>
                </div>
                <br>
                <br>
                <p id="message" align="center" style="color: darkred;"></p>
                <div class="ui fluid center aligned container">
                    <button id="download" class="ui active button">
                        <i class="download icon"></i>
                        Загрузить
                    </button>
                    <img id="spinner" style="width: 7rem; display: none;" src="static/spinner.gif" />
                </div>
                <br>
                <div class="ui raised padded">
                    <p align="center">Как найти ID группы:<br><i>https://guide.herzen.spb.ru/static/schedule_dates.php?id_group=<b><u>12460</u></b></i></p>
                    <p align="center">Арсений Величко 2021. <a href='https://github.com/arseniiarsenii/herzen-schedule-to-ics'>Код проекта на GitHub<i class="github icon"></i></a></p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>