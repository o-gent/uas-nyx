print("""
nnnn  nnnnnnnn yyyyyyy           yyyyyyyxxxxxxx      xxxxxxx
n:::nn::::::::nny:::::y         y:::::y  x:::::x    x:::::x 
n::::::::::::::nny:::::y       y:::::y    x:::::x  x:::::x  
nn:::::::::::::::ny:::::y     y:::::y      x:::::xx:::::x   
n:::::nnnn:::::n y:::::y   y:::::y        x::::::::::x    
n::::n    n::::n  y:::::y y:::::y          x::::::::x     
n::::n    n::::n   y:::::y:::::y           x::::::::x     
n::::n    n::::n    y:::::::::y           x::::::::::x    
n::::n    n::::n     y:::::::y           x:::::xx:::::x   
n::::n    n::::n      y:::::y           x:::::x  x:::::x  
n::::n    n::::n     y:::::y           x:::::x    x:::::x 
nnnnnn    nnnnnn    y:::::y           xxxxxxx      xxxxxxx
                    y:::::y                                
                    y:::::y                                 
                y:::::y                                  
                y:::::y                                   
                yyyyyyy                                    
                                                            
""")


from nyx import Main

import argparse

parser = argparse.ArgumentParser(description='run nyx')

parser.add_argument(
    '-s',
    '--sim',
    dest='simulated',
    help='enable SITL connection'
    )

args = parser.parse_args()

# convert the args to something useful, can probably do this differently
is_simulated = lambda x: True if x.simulated == "y" else True

main = Main(sim=is_simulated(args))
main.run()