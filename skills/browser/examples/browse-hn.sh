#!/bin/bash
# Simple: browse HN and read the front page
orb-browser deploy
orb-browser go https://news.ycombinator.com
orb-browser text
orb-browser sleep
