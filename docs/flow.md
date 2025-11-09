# Flow

Detailing the user flow as well as association with the marking scheme

The application consists of three main sections:
  - Reporting section
    - Form to input image of flytip, should output "scale" of flytipe for 1-3
    - Also contains location 

  - Impact section
    - Various figures determined by the scale and the location.
    - Crime level of flytipped areas
    - Social deprivation score of flytipped vs non flytipped
    - House price of flytipped vs non flytipped
    - environmental impacts of that scale of flytipping
    - Control for average in area
    - IMPACT STATEMENT AI: should interpret these results, and output a sentence talking about impact on individual circumstance.
      - in a format thats understandable, equate things for them

  - Solution section
    - Specific steps for remediation:
      - reporting flytipping for that local council
      - AI: Contain link to reporting site
      - General steps
      - Locations where rubbish can be thrown away
      - AI: PDF export for flyers that can be passed around the area
        - Community cohesion point


# TODO:

- Have the model determine the TYPE, SIZE, location (rural vs city, destroying our beautiful natural woods vs our kids are playing in trash type shit)? FEED INTO IMPACT SUMMARY
  - Household (furniture, matterses, general rubbish)
  - Construction ( Bricks, itmber asbestos)
  - Hazardous waste (Oils batteries chemicals)
  - Garden waste
  - Electrical
  - Furniture

- Flush out the API, do some checks to improve the quality of data it is getting
  - Mainly from a datasci PoV, will mainly be yousif
- 11 labs integration?
- look into support with forms using AI (ie yousifs idea)
- For the AI statement, feed it some data about the location to personalise it a bit (SEE THE FIRST POINT)
  - Leveraging AI to seamlessly build a persuasive, ready to ship argument to eliminate barriers for improving community responsibillity

