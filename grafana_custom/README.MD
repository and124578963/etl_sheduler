
TODO: Создать кастомный контейнер по графане, чтобы это все убрать из репозитория с кодом



1.Изначально папка build выгружена из контейнера графаны по пути /usr/share/grafana/public/build

2.Скрипт make_build_to_custombuild.sh делает замены в папке build и заменяет названия в графане на нужные. 
Необходимо запустить только 1 раз на папку build. 
Заменяет: 
 - Title 
 - приветствие над окном авторизации
 - Убирает из окна авторизации кнопки внизу страницы: ссылки на графану, версию и тп

3.Скрипт из custom_js.txt необходимо добавить в любой подключаемый js в графане из папки build
Он отключает для пользователей без прав админа верхнюю панель и кнопки редактирования секций дашборда.
Сейчас скрипт добавлен в ./build/app.b4a3702ce59b0c540886.js


4. favicon.png - и конка на вкладке браузера
5. logo.svg - все где отображался логотип графаны
6. gradient.svg - задний фон формы авторизации

Файлы и папки перезаписывают оригиналы через docker-compose.yaml

    volumes:
      - ./grafana_data:/var/lib/grafana
      - ./grafana_custom/build:/usr/share/grafana/public/build
      - ./grafana_custom/favicon.png:/usr/share/grafana/public/img/fav32.png
      - ./grafana_custom/favicon.png:/usr/share/grafana/public/img/apple-touch-icon.png
      - ./grafana_custom/logo.svg:/usr/share/grafana/public/img/grafana_icon.svg
      - ./grafana_custom/gradient.svg:/usr/share/grafana/public/img/g8_login_dark.svg
      - ./grafana_custom/gradient.svg:/usr/share/grafana/public/img/g8_login_light.svg





