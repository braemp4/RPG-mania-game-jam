from game_objects import DinoTest
import pygame 
import argparse

def test_sys():

    dino_test = DinoTest()
    dino_test.run_platformer()

parser = argparse.ArgumentParser()

parser.add_argument("--test", action="store_true")

args = parser.parse_args()

if args.test:
    test_sys()




