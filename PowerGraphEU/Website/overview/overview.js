
async function getData(){
    const response = await fetch ('http://localhost:5000/update_renewable_percentage?country=DE');
    const data = await response.json();
    const { non_renewable, renewable } = data;
    document.getElementById('greenValue').textContent = renewable+'MW';
    document.getElementById('fossilValue').textContent = non_renewable+'MW';
    
    
    console.log(`Test 1 Json: ${data} \n `)
    console.log(`Test 2 seperate Value: ${renewable,non_renewable}`)
    
}
getData()