//Var Declaration 
var ren_E_C1 
var ren_E_C2
var fos_E_C1
var fos_E_C2
var dates
var countryOne = undefined
var countryTwo = undefined
//Get JSON from API 

async function firstUpdateList (){ 
    countryOne = document.getElementById('country_one')
    let pathOne= `http://localhost:5000/percentage?country=${countryOne.value}`
    let response = await fetch (pathOne);
    let data = await response.json();
    let { date, renewable_percentage ,fossile_percentage } = data;
    dates = date;
    ren_E_C1 = renewable_percentage;
    fos_E_C1 = fossile_percentage;
    chart()
} 

async function secondUpdateList(){ 
    countryTwo = document.getElementById('country_two')
    let pathTwo= `http://localhost:5000/percentage?country=${countryTwo.value}`
    let response = await fetch (pathTwo);
    let data = await response.json();
    let { date, renewable_percentage ,fossile_percentage } = data;
    ren_E_C2 = renewable_percentage;
    fos_E_C2 = fossile_percentage;
    chart()
} 

//Chart 
function chart(){
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                //Country 1 Renewable
                label: `Renewable Energy ${countryOne.value}`,
                data: ren_E_C1,
                backgroundColor: [
                    'rgba(97, 245, 39, 0.63)'
                ],
                borderColor: [
                    'rgba(41, 144, 0, 0.63)'
                ],
                borderWidth: 1,
                stack:0,
            },
            {
                //Country 1 Fossil
                label: `Fossil Energy ${countryOne.value}`,
                data: fos_E_C1,
                backgroundColor: [
                    'rgba(193, 140, 68, 0.63)'
                    
                ],
                borderColor: [
                    'rgba(147, 84, 0, 0.63)',
                    
                ],
                borderWidth: 1,
                stack: 0,
            },{
                //Country 2 Renewable
                label: `Renewable Energy ${countryTwo.value}`,
                data: ren_E_C2,
                backgroundColor: [
                    'rgba(97, 245, 39, 0.63)'
                    
                ],
                borderColor: [
                    'rgba(41, 144, 0, 0.63)',
                    
                ],
                borderWidth: 1,
                stack: 1,
            },{
                //Country 2 Fossil
                label: `Fossil Energy ${countryTwo.value}`,
                data: fos_E_C2,
                backgroundColor: [
                    'rgba(193, 140, 68, 0.63)'
                    
                ],
                borderColor: [
                    'rgba(147, 84, 0, 0.63)',
                    
                ],
                borderWidth: 1,
                stack: 1,
            }

        ]
        },
        options: {
            responsive: true,
            scales: {
                x:{
                    stacked:true,
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
