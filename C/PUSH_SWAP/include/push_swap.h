/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: diwamoto <diwamoto@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/11 13:00:01 by diwamoto          #+#    #+#             */
/*   Updated: 2026/02/13 06:51:54 by diwamoto         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_SWAP_H
# define PUSH_SWAP_H

# include <stdlib.h>
# include <stddef.h>
# include <limits.h>

# include "../mylib/include/ft_printf.h"
# include "../mylib/include/libft.h"

typedef struct s_node
{
	int				value;
	int				index;
	struct s_node	*prev;
	struct s_node	*next;
}	t_node;

typedef struct s_stack
{
	t_node	*top;
	t_node	*bottom;
	int		size;
}	t_stack;

int		main(int argc, char **argv);
int		*parse_clarg(int argc, char **argv, int *size);
int		*parse_string(char *str, int *size);
int		*normalize(int size, int *values);
int		check_duplication(int *array, int size);
int		validate_args(char **argv, int count);
t_node	*create_list(int *values, int *indeces, int size);
t_stack	*init_stack(t_node *list, int size);

//algorithms
void	sort_a(t_stack *a, t_stack *b, int size);
void	quicksort(int *array, int left, int right);
void	radix_sort(t_stack *a, t_stack *b);
void	selectionsort_3(t_stack *a);
void	selectionsort_4_5(t_stack *a, t_stack *b);

//operations
void	pa(t_stack *a, t_stack *b);
void	pb(t_stack *a, t_stack *b);
void	ra(t_stack *a);
void	rra(t_stack *a);
void	sa(t_stack *a);

#endif
