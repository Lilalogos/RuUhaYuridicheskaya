# G2 — акты kad.arbitr.ru для сохранения (СТОП: скачивает Виталий)

kad.arbitr.ru отдаёт PDF только при открытии во вкладке браузера (скрипт и curl получают HTML-заглушку).
Порядок: открыть ссылку → в просмотрщике PDF кнопка «Скачать» → сохранить в ~/Downloads под исходным именем.

## А33-35161/2019 — АО «Авиакомпания «Нордстар» к Управлению Роспотребнадзора по Красноярскому краю
- [x] https://kad.arbitr.ru/Kad/PdfDocument/1982ab5f-d916-4b11-be5d-ee26555288ff/b9f92198-4f14-4198-803f-227777891c57/A33-35161-2019_20200129_Reshenie.pdf
- [ ] https://kad.arbitr.ru/Kad/PdfDocument/1982ab5f-d916-4b11-be5d-ee26555288ff/31ea5c01-822c-4778-bf2c-de5c9550cf74/A33-35161-2019_20200625_Postanovlenie_apelljacionnoj_instancii.pdf
- [ ] https://kad.arbitr.ru/Kad/PdfDocument/1982ab5f-d916-4b11-be5d-ee26555288ff/b632b5f7-2a15-4d8c-9eab-64dc7f3dee90/A33-35161-2019_20201023_Postanovlenie_kassacionnoj_instancii.pdf

## А33-536/2022 — АО «Авиакомпания «Нордстар» к Управлению Роспотребнадзора по Красноярскому краю
- [ ] https://kad.arbitr.ru/Kad/PdfDocument/e6c55098-9e64-4400-80db-79f6b967415f/7aff061e-aecf-4827-925f-ba74432eb3ae/A33-536-2022_20220324_Reshenie.pdf
- [ ] https://kad.arbitr.ru/Kad/PdfDocument/e6c55098-9e64-4400-80db-79f6b967415f/943686ce-3fed-4794-8a7a-31a6f1caba62/A33-536-2022_20220614_Postanovlenie_apelljacionnoj_instancii.pdf

## А40-284009/2021 — ООО «Деливери Клаб» к Управлению Роспотребнадзора по г. Москве
- [x] https://kad.arbitr.ru/Kad/PdfDocument/2bcdfab5-436c-4b74-835f-7b99744e87d4/11f4da62-4d03-4113-bc36-275b523ec906/A40-284009-2021_20220318_Reshenija_i_postanovlenija.pdf
- [x] https://kad.arbitr.ru/Kad/PdfDocument/2bcdfab5-436c-4b74-835f-7b99744e87d4/2b05d65e-b2e8-47fa-83f0-c9e8f0130a6a/A40-284009-2021_20220530_Postanovlenie_apelljacionnoj_instancii.pdf
- [x] https://kad.arbitr.ru/Kad/PdfDocument/2bcdfab5-436c-4b74-835f-7b99744e87d4/12f3aa1c-5a3d-4243-b6b8-b6d18de06de7/A40-284009-2021_20220914_Reshenija_i_postanovlenija.pdf
- [x] https://kad.arbitr.ru/Kad/PdfDocument/2bcdfab5-436c-4b74-835f-7b99744e87d4/55b1044f-9252-4441-ba2b-b9944062c7fc/A40-284009-2021_20221212_Reshenija_i_postanovlenija.pdf
- [x] https://kad.arbitr.ru/Kad/PdfDocument/2bcdfab5-436c-4b74-835f-7b99744e87d4/c45f1901-d145-438a-bb16-d048125ce924/A40-284009-2021_20230213_Postanovlenie_apelljacionnoj_instancii.pdf
- [x] https://kad.arbitr.ru/Kad/PdfDocument/2bcdfab5-436c-4b74-835f-7b99744e87d4/bf4a80e5-f554-4d11-9c56-d87248c91df9/A40-284009-2021_20230531_Postanovlenie_kassacii.pdf


## Итог
- Получено 7 из 11 (папка ~/Downloads/FireShot/). Не получены: А33-35161/2019 апелляция и кассация; А33-536/2022 оба акта.

## Повторная попытка 2026-10-04 (прогон «сбор пробелов»)
- curl/скрипт с Referer и Accept: application/pdf → по-прежнему HTML-заглушка с pravocaptcha (3 710 байт). Четыре PDF выше (А33-35161/2019 апелляция и кассация; А33-536/2022 решение и апелляция) остаются СТОПом: скачивает Виталий.
- Дополнительно к списку: карточка А33-14061/2022 (поиск в картотеке сбрасывается), А60-36566/2023 (Ф09-7782/24) — содержание не проверено.
