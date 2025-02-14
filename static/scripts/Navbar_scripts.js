const dropdown = document.querySelector('#accountdropdown');
const account = document.querySelector('#account');

document.getElementById('account').addEventListener('click', toggleDropdown);
function toggleDropdown(event) {
  event.stopPropagation(); //somehow adding event to the function and
  //stopping propagation allows children image to trigger the onclick() function
  if (dropdown.style.display != 'flex')
    dropdown.style.display = 'flex';
  else
    dropdown.style.display = 'none';
}
// Close overlay when clicking outside of it
window.addEventListener('click', (event) => {
  if (event.target != account)
    dropdown.style.display = 'none';
});

// Function to log a message
function handleCredentialResponse(response) {
  const userToken = jwt_decode(response.credential);
  console.log('User Information:');
  console.log(`Name: ${userToken.name}`);
  console.log(`Email: ${userToken.email}`);
  console.log(`Profile Picture: ${userToken.picture}`);
}
