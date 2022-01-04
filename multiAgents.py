# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util


from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)     

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """
    def minmax(self, depth,agentIndex,gameState,maximAgent = 0):
        numAgents = gameState.getNumAgents()
        #If the gamestate is winning, loosing or the depth is zero we don't create new branches, but we to static evaluations instead
        if gameState.isLose() or gameState.isWin() or depth == 0:
            #We always return an array of the static score, and the move done to reach it from one not up in the tree
            return [gameState.getScore(),None]
        else: 
            if agentIndex == 0:
                #maxEval = -2**10 #- inf, so that every iteration will always find one of the legal moves best
                legalMoves = gameState.getLegalActions(agentIndex)
                #We want to chose the first branch as best branch in the first iteration every time, and then see if any other alternatives
                #are better
                count = 0
                for action in legalMoves:
                    #generate new gamestate identiacal, but with pacman moved in action direction
                    newGameState = gameState.generateSuccessor(agentIndex, action) 
                    #If the next layer in the minmax tree are the leafnodes, we check for win and loss with assigning a huge number
                    #as win, and a small number as loss.
                    Eval = self.minmax(depth, agentIndex + 1, newGameState)
                    if count == 0:
                        maxEval = Eval[0]
                        corresponding_action = action
                    ###We choose the smallest evaluation from the ghosts below
                    elif maxEval<Eval[0]:
                        maxEval = Eval[0]
                        corresponding_action = action
                    count +=1
                return [maxEval,corresponding_action]
            else:
                #minEval = 2**10
                legalMoves = gameState.getLegalActions(agentIndex)
                count = 0
                for action in legalMoves:
                    #generate new gamestate identiacal, but with the ghost moved in action direction
                    newGameState = gameState.generateSuccessor(agentIndex, action) 
                    #Does not go one layer down in the tree before all ghosts have moved
                    #, and then goes to the next agent(and back to packman at mod numAgents)
                    #Goes down 1 depth each time we go back to packman
                    if (agentIndex + 1)%numAgents == 0:
                        Eval = self.minmax(depth - 1, 0, newGameState)
                    else:
                        Eval = self.minmax(depth, agentIndex + 1, newGameState)
                    if count == 0:
                        minEval = Eval[0]
                        corresponding_action = action
                    elif minEval>Eval[0]:
                        minEval = Eval[0]
                        corresponding_action = action
                    count += 1
                
                return [minEval, corresponding_action]

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()
        return self.minmax(self.depth,0,gameState)[1]

  
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        return self.alphaBeta(self.depth,0,gameState, alpha = -2**16, beta = 2**16)[1]
        #util.raiseNotDefined()

    def alphaBeta(self, depth,agentIndex,gameState,alpha,beta,maximAgent = 0):
        numAgents = gameState.getNumAgents()
        #If the gamestate is winning, loosing or the depth is zero we don't create new branches, but we to static evaluations instead
        if gameState.isLose() or gameState.isWin() or depth == 0:
            return [gameState.getScore(),None]
        else: 
            if agentIndex == 0:
                maxEval, corresponding_action = -2**16, None #- inf, so that every iteration will always find one of the legal moves best
                #We want to chose the first branch as best branch in the first iteration every time, and then see if any other alternatives
                #are better
                #Creating a new branch for each legal move
                for action in gameState.getLegalActions(agentIndex):
                    #generate new gamestate identiacal, but with pacman moved in action direction
                    newGameState = gameState.generateSuccessor(agentIndex, action) 
                    #If the next layer in the minmax tree are the leafnodes, we check for win and loss with assigning a huge number
                    #as win, and a small number as loss.
                    Eval = self.alphaBeta(depth, agentIndex + 1, newGameState, alpha, beta)
                    ###We choose the smallest evaluation from the ghosts below
                    if maxEval<Eval[0]:
                        maxEval = Eval[0]
                        corresponding_action = action
                        # alpha = max(alpha,maxEval)
                    ###Pruning part, here we prune of the branches the instant they can't be the maximized path
                    # alpha = max(alpha,maxEval)
                    if maxEval > beta:
                        return [maxEval,corresponding_action]
                    alpha = max(alpha,maxEval)
                    best_move = [maxEval, corresponding_action]
            else:
                minEval, corresponding_action = 2**16, None
                #Checking if next agent is pacman or ghost outside of the loop to avoid needless computations.
                if (agentIndex + 1)%numAgents == 0:
                    depth -= 1
                    agentIndex = -1
                    
                for action in gameState.getLegalActions(agentIndex):
                    #generate new gamestate identiacal, but with the ghost moved in action direction
                    newGameState = gameState.generateSuccessor(agentIndex, action) 
                    #Does not go one layer down in the tree before all ghosts have moved
                    #, and then goes to the next agent(and back to packman at mod numAgents)
                    #Goes down 1 depth each time we go back to packman
                    # if (agentIndex + 1)%numAgents == 0:
                    #     Eval = self.alphaBeta(depth - 1, 0, newGameState, alpha, beta)
                    # else:
                    #     Eval = self.alphaBeta(depth, agentIndex + 1, newGameState, alpha, beta)
                    Eval = self.alphaBeta(depth, agentIndex + 1, newGameState, alpha, beta)
                    if minEval > Eval[0]:
                        minEval = Eval[0]
                        corresponding_action = action
                        # beta = min(beta,minEval)
                    
                    ###Pruning part
                    # beta = min(beta,minEval)
                    if minEval < alpha:
                        return [minEval, corresponding_action]
                    beta = min(beta,minEval)
                    best_move = [minEval, corresponding_action]
            return best_move

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()
        

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
#   python3 autograder.py -q q2
#   python3 autograder.py -q q2 --no-graphics
#   python3 autograder.py -q q3
#   python autograder.py -q q3 --no-graphics
    