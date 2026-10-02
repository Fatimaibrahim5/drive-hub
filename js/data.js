const CARS = [
  {
    id: "mercedes",
    brand: "Mercedes-Benz",
    model: "C 200 Sedan",
    year: 2023,
    price: 46900,
    mileage: 12400,
    engine: "2.0L Turbo 4-cylinder, mild hybrid",
    power: 201,
    transmission: "9-speed automatic",
    fuel: "Petrol (mild hybrid)",
    mpg: 34,
    drive: "Rear-wheel drive",
    seats: 5,
    color: "Obsidian Black",
    front: "image/mercedes.jpg",
    back: "image/mercedes-back.jpg",
    specs: [
      "LED High Performance headlights",
      "MBUX infotainment with 11.9\" touchscreen",
      "Heated leather seats",
      "Parking assist with 360° camera",
      "Adaptive cruise control",
      "Ambient lighting (64 colours)"
    ],
    description:
      "A refined, quiet executive sedan with a luxurious cabin and a smooth mild-hybrid powertrain. One owner, full service history and in showroom condition."
  },
  {
    id: "audi",
    brand: "Audi",
    model: "A4 40 TFSI S line",
    year: 2022,
    price: 38500,
    mileage: 21300,
    engine: "2.0L TFSI turbo 4-cylinder",
    power: 201,
    transmission: "7-speed S tronic dual-clutch",
    fuel: "Petrol",
    mpg: 36,
    drive: "Front-wheel drive",
    seats: 5,
    color: "Manhattan Grey",
    front: "image/audi.jpg",
    back: "image/audi-back.jpg",
    specs: [
      "Matrix-style LED headlights",
      "Audi virtual cockpit",
      "S line sport seats",
      "Bang & Olufsen sound system",
      "Lane assist and traffic sign recognition",
      "Wireless smartphone charging"
    ],
    description:
      "A sharp, sporty-looking sedan that is as comfortable on the motorway as it is in the city. Efficient engine, a very strong tech package and low running costs."
  },
  {
    id: "bmw",
    brand: "BMW",
    model: "330i M Sport",
    year: 2023,
    price: 43200,
    mileage: 9800,
    engine: "2.0L TwinPower Turbo 4-cylinder",
    power: 255,
    transmission: "8-speed Steptronic automatic",
    fuel: "Petrol",
    mpg: 32,
    drive: "Rear-wheel drive",
    seats: 5,
    color: "Skyscraper Grey",
    front: "image/bmw.avif",
    back: "image/bmw-back.png",
    specs: [
      "M Sport suspension and brakes",
      "BMW Live Cockpit Professional",
      "Harman Kardon surround sound",
      "Laser-ready LED headlights",
      "Head-up display",
      "Comfort access keyless entry"
    ],
    description:
      "The driver's choice. Rear-wheel drive balance, strong turbo power and an M Sport package that makes every road more fun. Barely used and still under manufacturer warranty."
  }
];

function formatPrice(n) {
  return "$" + Number(n).toLocaleString("en-US");
}

function formatMiles(n) {
  return Number(n).toLocaleString("en-US") + " mi";
}

function getCar(id) {
  return CARS.find(function (c) { return c.id === id; });
}
