
private function checkClosed():Boolean
{
    if (this._willClose)
    {
        if (this._asyncTrees.length == 0)
        {
            this._willClose = false;
            this.dispatchEvent(new Event(Event.CLOSE));
        }
        return true;
    }
    return false;
}