using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;

public class GameBoard : MonoBehaviour
{
    // Start is called before the first frame update
    [SerializeField] private Tilemap currentState;  // Tilemap only take Vector3Int
    [SerializeField] private Tilemap nextState;
    [SerializeField] private Tile aliveTile;
    [SerializeField] private Tile deadTile;
    [SerializeField] private Pattern pattern;
    [SerializeField] private float updateInterval = 0.05f;
    
    private HashSet<Vector3Int> aliveCells;
    private HashSet<Vector3Int> cellsToCheck; 

    private void Awake()
    {
        aliveCells = new HashSet<Vector3Int>();
        cellsToCheck = new HashSet<Vector3Int>();
    }

    private void Start()
    {
        SetPattern(pattern);
    }

    private void SetPattern(Pattern pattern)
    {
        Clear();

        Vector2Int center = pattern.GetCenter();
        Vector3Int left = new Vector3Int(-40,0,0);
        Vector3Int right = new Vector3Int(40,0,0);
        Vector3Int up = new Vector3Int(0,40,0);
        Vector3Int down = new Vector3Int(0,-40,0);

        for(int i=0; i<pattern.cells.Length; i++){
            Vector3Int cell = (Vector3Int)(pattern.cells[i] - center);
            Vector3Int cell1 = (Vector3Int)(pattern.cells[i] - center) + left;
            Vector3Int cell2 = (Vector3Int)(pattern.cells[i] - center) + right;
            Vector3Int cell3 = (Vector3Int)(pattern.cells[i] - center) + up;
            Vector3Int cell4 = (Vector3Int)(pattern.cells[i] - center) + down;
            currentState.SetTile(cell, aliveTile);
            currentState.SetTile(cell1, aliveTile);
            currentState.SetTile(cell2, aliveTile);
            currentState.SetTile(cell3, aliveTile);
            currentState.SetTile(cell4, aliveTile);
            aliveCells.Add(cell);
            aliveCells.Add(cell1);
            aliveCells.Add(cell2);
            aliveCells.Add(cell3);
            aliveCells.Add(cell4);
        }

    }

    private void Clear()
    {
        //currentState.ClearAllTiles();
        //nextState.ClearAllTiles();
        aliveCells.Clear();
        cellsToCheck.Clear();
        currentState.ClearAllTiles();
        nextState.ClearAllTiles();
    }

    private void OnEnable()
    {
        StartCoroutine(Simulate());
    }

    private IEnumerator Simulate()
    {
        var interval = new WaitForSeconds(updateInterval);
        while(enabled){
            UpdateState();
            yield return interval;
        }
        
    }

    private void UpdateState()
    {
        cellsToCheck.Clear();

        // gather cells to check
        foreach (Vector3Int cell in aliveCells)
        {
            for(int x=-1; x<=1; x++)
            {
                for(int y=-1; y<=1; y++)
                {
                    cellsToCheck.Add(cell + new Vector3Int(x,y,0));
                }
            }
        }

        // transitioning cells to the next state
        foreach( Vector3Int cell in cellsToCheck)
        {
            // TODO
            int neighbors = CountNeighbors(cell);
            bool alive = IsAlive(cell);
            if(!alive && neighbors==3)
            {
                // becomes alive
                nextState.SetTile(cell, aliveTile);
                aliveCells.Add(cell);
            }
            else if(alive && (neighbors <2 || neighbors>3))
            {
                // becomes dead
                nextState.SetTile(cell, deadTile);
                aliveCells.Remove(cell);
            }
            else    // no change
            {
                // stays the same
                nextState.SetTile(cell, currentState.GetTile(cell));
            }
        }

        // swap current state with next state
        Tilemap temp = currentState;
        currentState = nextState;
        nextState = temp;
        nextState.ClearAllTiles();
    }

    private int CountNeighbors(Vector3Int cell)
    {
        int count = 0;

        for(int x = -1; x<=1; x++)
        {
            for(int y = -1; y<=1; y++)
            {
                Vector3Int neighbor = cell + new Vector3Int(x,y,0);

                if(x==0 && y==0)
                {
                    continue;
                }
                else if(IsAlive(neighbor))
                {
                    count++;
                }
            }
        }

        return count;
    }
    
    private bool IsAlive(Vector3Int cell)
    {
        return currentState.GetTile(cell)==aliveTile;
    }
