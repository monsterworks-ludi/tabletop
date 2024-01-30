//
//  main.c
//  damage
//
//  Created by Aaron Montgomery on 1/29/24.
//

#include <stdio.h>
#include "gmp-6.3.0/gmp.h"

int size(int hand[4])
{
	return hand[0] + hand[1] + hand[2] + hand[3];
}

int white_damage(int hand[4])
{
	return 1*hand[1] + 2*(hand[2] + hand[3]);
}

float damage(int deck[4], int hand[4], int cards, float probability)
{
	
	if (size(hand) == cards + hand[3])
	{
		return white_damage(hand)*probability;
	}

	float dam = 0;
	for (int card_type = 0; card_type < 4; card_type++)
	{
		if (deck[card_type] > 0)
		{
			float prob = (float)deck[card_type]/size(deck);
			deck[card_type] -= 1;
			hand[card_type] += 1;
			if (cards < size(hand) || hand[0] < 2)
			{
				dam += damage(deck, hand, cards, prob*probability);
			}
			deck[card_type] += 1;
			hand[card_type] -= 1;
		}
	}
	return dam;
}


void mpq_set_white_damage(mpq_t result, int hand[4])
{
	mpq_set_ui(result, white_damage(hand), 1);
}

void mpq_set_damage(mpq_t result, int deck[4], int hand[4], int cards, mpq_t probability)
{
	
	if (size(hand) == cards + hand[3])
	{
		mpq_t damage;
		mpq_init(damage);
		mpq_set_white_damage(damage, hand);
		mpq_mul(result, damage, probability);
		return;
	}
	
	mpq_t damage;
	mpq_init(damage);
	mpq_set_ui(damage, 0, 1);
	for (int card_type = 0; card_type < 4; card_type++)
	{
		if (deck[card_type] > 0)
		{
			int num = deck[card_type];
			int den = size(deck);
			deck[card_type] -= 1;
			hand[card_type] += 1;
			if (cards < size(hand) || hand[0] < 2)
			{
				mpq_t prob;
				mpq_init(prob);
				mpq_set_ui(prob, num, den);
				mpq_mul(prob, probability, prob);
				mpq_t new_damage;
				mpq_init(new_damage);
				mpq_set_damage(new_damage, deck, hand, cards, prob);
				mpq_add(damage, damage, new_damage);
			}
			deck[card_type] += 1;
			hand[card_type] -= 1;
		}
	}
	mpq_set(result, damage);
}



int main(int argc, const char * argv[])
{
	printf("Small Deck with Rational Output\n");
	int deck[4] = {6, 6, 3, 3};
	int hand[4] = {0, 0, 0, 0};
		for (int i = 0; i < 11; i++)
		{
			mpq_t result;
			mpq_init(result);
			mpq_set_ui(result, 0, 1);
			mpq_t mpq_1;
			mpq_init(mpq_1);
			mpq_set_ui(mpq_1, 1, 1);
			mpq_set_damage(result, deck, hand, i, mpq_1);
			printf("HAND SIZE: %d\t", i); mpq_out_str(stdout,10,result); printf("\n");
		}
	
	printf("Large Deck with Rational Output\n");
	deck[0] = deck[1] = 30;
	deck[2] = deck[3] = 15;
	for (int i = 0; i < 8; i++)
	{
		mpq_t result;
		mpq_init(result);
		mpq_set_ui(result, 0, 1);
		mpq_t mpq_1;
		mpq_init(mpq_1);
		mpq_set_ui(mpq_1, 1, 1);
		mpq_set_damage(result, deck, hand, i, mpq_1);
		printf("HAND SIZE: %d\t", i); mpq_out_str(stdout,10,result); printf("\n");
	}
	
	printf("Large Deck with Float Output\n");
	for (int i = 8; i < 11; i++)
	{
		printf("HAND SIZE: %d\t%0.6f\n", i, damage(deck, hand, i, 1));
	}
	return 0;
}
