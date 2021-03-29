<html>
<head>
   <title>Herzen Schedule Export</title>
   <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.css"></link>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.js"></script>
</head>
<body>
    <div><br><br></div>
    <div class="ui centered grid">
    <div class="ui centered raised padded container segment">
        <h1 class="ui center aligned header"><u>Herzen Schedule Export</u></h1>
        <h4 class="ui center aligned header ">Экспорт расписания вашей группы в файл iCalendar (.ics) с возможностью последующего импорта в Google календарь и другие календари.</h2>
        <div class="ui center aligned segment" style="size: inherit;">
            <form method=POST>
                <div class="ui top attached label compact">Данные</div>
                <div> ID группы </div>
                <div class="ui left icon input compact">
                    <input type="text" placeholder="12460" name='group_id'>
                    <i class="users icon"></i>
                </div>
                <div> Номер подгруппы </div>
                <div class="ui left icon input compact">
                    <input type="text" placeholder="Если нет - 1" name='subgroup'>
                    <i class="users icon"></i>
                </div>
                <br><br>
                <div class="ui center aligned container">
                    <button class="ui active button" type='submit'>
                        <i class="download icon"></i>
                        Загрузить
                    </button>
                </div>
                <br>
                <div class="ui raised padded">
                    <p align="center">Как найти ID группы:<br><i>https://guide.herzen.spb.ru/static/schedule_dates.php?id_group=<b><u>12460</u></b></i></p>
                    <p align="center">Арсений Величко 2021. <a href='https://github.com/arseniiarsenii/herzen-schedule-to-ics'>Код проекта на GitHub<i class="github icon"></i></a></p>
                </div>
            </form>
        </div>
    </div>
    </div>
</body>
</html>