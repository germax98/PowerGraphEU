# PowerGraphEU

#Description 
Das PowerGraphEU ist eine Fullstack Webapplication, welche es ermöglicht die aktuelle Energieproduktion von Fossilen und Erneuerbaren Energien aller Europäischen Ländern in Echtzeit miteinander zu vergleichen. Das Projekt war ein Studienprojekt und wurde in Teamarbeit angefertig. 
Die Arbeit wurde in den Bereich Backend und Frontend aufgeteilt. Mein Teil der Arbeit war das erstellen des UI/UX Design sowie die Umsetzung des Frontends.
Mein Teampartner übernahm die Entwicklung des Backends.


## Frontend 

Die Website besteht aus drei unterschiedlichen Pages. 

  1. Die Overview besteht aus der aktuellen EnergieProduktion des gewünschten Landes und liefert Daten über die aktuelle erneuerbare und Fossile Energie Produktion des Landes.

  2. die Seite Devices konnte aufgrund von Zeitgründen nicht fertig gestellt werden. Es sollte hierbei möglich sein, diverse Geräte anzulegen, um den Ladezyclus der Geräte so zu bestimmen, dass die Verbraucher mit erneuerbarer Energie betrieben werden. 
  
  3. Die Seite Charts ermöglicht es dem Nutzer die Europäische Energie Produktion einzelner europäischer Länder miteinander zu vergleichen. Die Daten werden hierbei mithilfe von Chart JS dargestellt.

### Technologies Used:

- HTML
- CSS
- JavaScript
- Chart JS

### Backend

Das Backend wurde mit Python entwickelt. Hierfür kam das Framework Flask zum einsatz, welches die Schnittstelle zwischen dem Frontend und dem Backend ermöglicht. Es wird außerdem im Backend ein API Request gestellt womit die Daten Empfangen werden. Diese werden im Backend ausgewertet und mithilfe von mongodb abgespeichert. Das gesamte Projekt wurde anschließend auf einem Rasberry pie Lokal gehostet.

### Technologies Used:

- Python
- Flask
- MongoDB
- Rasberry Pie

# Author 

Max Wölfel
