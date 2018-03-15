# Wine Shop
A wine shop implementing wine library, wine search, new wine input and shopping
cart.
The GAE link: https://wineshop-zeyu-chen.appspot.com/

## Category
Four default categories are implemented: red, rose, white and sparkling.

## Search
Allow partial search and capital insensitive. The partial search means that once
the string input is contained by the specific tag, the search engine will show
the result.

## Enter New Wine
User must input all fields to input the element.

## Shopping Cart
Shopping cart is binded to the user through unique user id, that agrees to the
REST-ful design. Additionally, the app supports temporary cart. Customers can
merge their items before after login. The method is using cookie as an id to mark
the temporary visitor
