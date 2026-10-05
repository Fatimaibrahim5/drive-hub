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
    interior: "image/mercedes-interior.jpeg",
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
    interior: "image/audi-interior.jpeg",
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
    interior: "image/bmw-interior.jpeg",
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
  },
  {
    id: "glc",
    brand: "Mercedes-Benz",
    model: "GLC 300 4MATIC Coupe",
    year: 2023,
    price: 52900,
    mileage: 14200,
    engine: "2.0L Turbo 4-cylinder, mild hybrid",
    power: 255,
    transmission: "9-speed automatic",
    fuel: "Petrol (mild hybrid)",
    mpg: 28,
    drive: "All-wheel drive",
    seats: 5,
    color: "Graphite Grey",
    front: "image/glc.jpg",
    back: "image/glc-back.png",
    interior: "image/glc-interior.jpeg",
    specs: [
      "4MATIC permanent all-wheel drive",
      "MBUX with 11.9\" touchscreen",
      "Panoramic sunroof",
      "Heated and ventilated front seats",
      "360° camera with parking assist",
      "Power tailgate"
    ],
    description:
      "A stylish SUV coupe that mixes a sloping, sporty roofline with the comfort and quality Mercedes is known for. All-wheel drive makes it confident in any weather, and the cabin is spacious and well equipped."
  },
  {
    id: "bmw8",
    brand: "BMW",
    model: "M850i xDrive Coupe",
    year: 2022,
    price: 79900,
    mileage: 11600,
    engine: "4.4L twin-turbo V8",
    power: 523,
    transmission: "8-speed Steptronic Sport automatic",
    fuel: "Petrol",
    mpg: 21,
    drive: "All-wheel drive",
    seats: 4,
    color: "Frozen Black",
    front: "image/bmw8.webp",
    back: "image/bmw8-back.jpg",
    interior: "image/bmw8-interior.jpeg",
    specs: [
      "M Sport brakes and Adaptive M suspension",
      "Integral Active Steering",
      "BMW Laserlight headlights",
      "Bowers & Wilkins Diamond surround sound",
      "Head-up display",
      "Carbon fibre roof"
    ],
    description:
      "A true grand tourer: a thundering twin-turbo V8, a beautiful coupe body and a first-class cabin. Fast enough to thrill, comfortable enough for a long trip."
  },
  {
    id: "porsche911",
    brand: "Porsche",
    model: "911 S/T",
    year: 2024,
    price: 289900,
    mileage: 1900,
    engine: "4.0L naturally aspirated flat-six",
    power: 518,
    transmission: "6-speed manual",
    fuel: "Petrol",
    mpg: 17,
    drive: "Rear-wheel drive",
    seats: 2,
    color: "Oak Green Metallic",
    front: "image/porshe911.webp",
    back: "image/porshe911-back.webp",
    interior: "image/porshe911-interior.jpeg",
    specs: [
      "Lightweight carbon fibre bonnet and roof",
      "Rear-axle steering",
      "Porsche Active Suspension Management",
      "Ceramic composite brakes",
      "Sport Chrono package",
      "Heritage \"72\" livery with centre-lock wheels"
    ],
    description:
      "A rare, driver-focused 911 with a high-revving naturally aspirated flat-six and a pure six-speed manual gearbox. Barely driven, collector condition and a true highlight of our showroom."
  },
  {
    id: "s63",
    brand: "Mercedes-AMG",
    model: "S 63 4MATIC+",
    year: 2019,
    price: 94900,
    mileage: 28700,
    engine: "4.0L twin-turbo V8",
    power: 603,
    transmission: "9-speed AMG Speedshift MCT",
    fuel: "Petrol",
    mpg: 19,
    drive: "All-wheel drive",
    seats: 5,
    color: "Polar White",
    front: "image/s63.jpeg",
    back: "image/s63-back.jpeg",
    interior: "image/s63-interior.jpeg",
    specs: [
      "AMG Ride Control air suspension",
      "AMG Performance steering wheel",
      "Burmester surround sound system",
      "Nappa leather with diamond-quilted seats",
      "Multibeam LED headlights",
      "Head-up display"
    ],
    description:
      "The flagship Mercedes saloon with an AMG twin-turbo V8 and a cabin that feels like a first-class lounge. As calm as a limousine and as fast as a sports car."
  },
  {
    id: "svr",
    brand: "Land Rover",
    model: "Range Rover Sport SVR",
    year: 2020,
    price: 89900,
    mileage: 24500,
    engine: "5.0L supercharged V8",
    power: 567,
    transmission: "8-speed automatic",
    fuel: "Petrol",
    mpg: 16,
    drive: "All-wheel drive",
    seats: 5,
    color: "Estoril Blue",
    front: "image/svr.jpeg",
    back: "image/svr-back.jpeg",
    interior: "image/svr-interior.jpeg",
    specs: [
      "Dynamic Response active suspension",
      "SVR performance seats in leather and suede",
      "Active exhaust with sports mode",
      "Meridian surround sound system",
      "Panoramic sunroof",
      "Terrain Response 2 with all-wheel drive"
    ],
    description:
      "The fastest, loudest Range Rover Sport: a supercharged V8 in a luxury SUV body with a bold Estoril Blue finish and a leather interior. Powerful on the road and capable off it."
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
