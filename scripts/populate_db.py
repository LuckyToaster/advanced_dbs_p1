from ODM import initApp 

initApp(scope=globals()) 

upm = EducationalCentre(name='Universidad Politecnica de Madrid', website='upm.es', year_founded=1971, address='Av. Complutense, s/n, Moncloa - Aravaca, 28040 Madrid')
upm.save()
uam = EducationalCentre(name='Universidad Autónoma de Madrid', website='uam.es', year_founded=1968, address='C. Francisco Tomás y Valiente, 5, Fuencarral-El Pardo, 28049 Madrid') 
uam.save()
ucm = EducationalCentre(name='Universidad Complutense de Madrid', website='ucm.es', year_founded=1293, address='Av. Complutense, s/n, Moncloa - Aravaca, 28040 Madrid')
ucm.save()
utad = EducationalCentre(name='U-TAD: Centro Universitario de Tecnologia y Arte Digital', website='u-tad.com', year_founded=2011, address='C. Playa de Liencres, 2 bis, 28290 Las Rozas de Madrid, Madrid')
utad.save()
ub = EducationalCentre(name='Universitat de Barcelona', website='ub.edu', year_founded=1450, address='Gran Via de les Corts Catalanes, 585, 08007 Barcelona, España')
ub.save()
ulpgc = EducationalCentre(name='Universidad de Las Palmas de Gran Canaria', website='ulpgc.es', year_founded=1989, address='Campus Universitario de Tafira, 35017 Las Palmas de Gran Canaria, Islas Canarias, España')
ulpgc.save()

deloitte = Company(name='Deloitte', cif='D45678901', website='deloitte.com/es', address='Torre Picasso Madrid, Madrid 28020 España')
deloitte.save()
accenture = Company(name='Accenture', cif='C34567890', website='accenture.com/es', address='P.º de la Castellana, 85, Tetuán, 28046 Madrid')
accenture.save()
microsoft = Company(name='Microsoft', cif='B23456789', website='microsoft.com/es-es/')
microsoft.save()
google = Company(name='Google', cif='B12345678', website='google.es', address='C. de San Germán, 10, Tetuán, 28020 Madrid')
google.save()
startup = Company(name='Custom Solutions SA', cif='C12345678', website='customsolutions.es', address='Avenida de Europa 10, Pozuelo de Alarcón, Madrid, 28223 España')
startup.save()

p1 = Person(
    name='alex',
    email='alex@email.com',
    description='I like Software Engineering and AI, did i mention i really love AI?',
    address='Calle Triana, 56, 35002 Las Palmas de Gran Canaria, Islas Canarias, España',
    company=microsoft._id,
    education=[{'name': 'computer science', 'year_graduated': 2026, 'education_centre': upm._id}]
) 

p1.save()
p2 = Person(
    name='clara', 
    email='clara@email.com', 
    description='I am passionate about programming, Machine Learning and Data Science',
    address='Avinguda Diagonal, 640, 08017 Barcelona, España',
    company=microsoft._id,
    education=[ {'name': 'computer science', 'year_graduated': 2020, 'education_centre': uam._id}, {'name': 'data science', 'year_graduated': 2024, 'education_centre': utad._id} ]
)
p2.save()

p3 = Person(
    name='lucas',
    email='lucas@email.com',
    description='Software engineer interested in backend systems.',
    address='Carrer de Balmes, 200, 08006 Barcelona, España',
    company=deloitte._id,
    education=[ {'name': 'computer engineering', 'year_graduated': 2019, 'education_centre': ucm._id} ]
)
p3.save()

p4 = Person(
    name='maria',
    email='maria@email.com',
    description='Data analyst with experience in machine learning.',
    address='Calle de Serrano, 110, 28006 Madrid, España',
    company=deloitte._id,
    education=[ {'name': 'data science', 'year_graduated': 2022, 'education_centre': uam._id} ]
)
p4.save()

p5 = Person(
    name='javier',
    email='javier@email.com',
    description='Web developer specialized in frontend frameworks. vibe coding with Artificial Intelligence #AI',
    address='Paseo del Prado, 28, 28014 Madrid, España',
    company=accenture._id,
    education=[ {'name': 'multimedia engineering', 'year_graduated': 2021, 'education_centre': utad._id} ]
)
p5.save()

p6 = Person(
    name='sofia',
    email='sofia@email.com',
    description='Cloud computing enthusiast and DevOps engineer, and i like BIG DATA yo.',
    address='Calle de Alcalá, 45, 28014 Madrid, España',
    company=google._id,
    education=[
        {'name': 'computer science', 'year_graduated': 2018, 'education_centre': upm._id},
        {'name': 'information systems', 'year_graduated': 2020, 'education_centre': ucm._id}
    ]
)
p6.save()

p7 = Person(
    name='diego',
    email='diego@email.com',
    description='AI researcher working on natural language processing.',
    address='Calle de Serrano, 55, 28006 Madrid, España',
    company=google._id,
    education=[{'name': 'computer science', 'year_graduated': 2017, 'education_centre': upm._id}]
)
p7.save()

p8 = Person(
    name='laura',
    email='laura@email.com',
    description='Software engineer focusing on cloud infrastructure.',
    address='Paseo de la Castellana, 150, 28046 Madrid, España',
    company=startup._id,
    education=[{'name': 'software engineering', 'year_graduated': 2019, 'education_centre': uam._id}]
)
p8.save()

p9 = Person(
    name='marc',
    email='marc@email.com',
    description='Front-end developer student interested in web technologies.',
    address='Carrer de Balmes, 250, 08006 Barcelona, España',
    company=startup._id,
    education=[{'name': 'computer science', 'year_graduated': 2026, 'education_centre': ub._id}]
)
p9.save()

p10 = Person(
    name='ana',
    email='ana@email.com',
    description='Aspiring data scientist passionate about machine learning.',
    address='Calle Mayor de Triana, 120, 35002 Las Palmas de Gran Canaria, Islas Canarias, España',
    company=startup._id,
    education=[{'name': 'data science', 'year_graduated': 2025, 'education_centre': ulpgc._id}]
)
p10.save()

